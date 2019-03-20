using System;
using System.Collections.Generic;
using System.IO;
using System.Net.Http;
using System.Threading.Tasks;
using Xamarin.Forms;

namespace OrderMeal
{

    public partial class SelectMealOptions : ContentPage
    {
        private int optionOneMealOrders = 0;
        private int optionTwoMealOrders = 0;

        public SelectMealOptions()
        {
            InitializeComponent();

            op1qty.Text = optionOneMealOrders.ToString();
            op2qty.Text = optionTwoMealOrders.ToString();

            getimg();
        }

        async void Handle_Clicked(object sender, System.EventArgs e)
        {
            if (optionOneMealOrders == 0 && optionTwoMealOrders == 0) 
            {
                await DisplayAlert("Order Error", "Please make an order to continue", "Continue");
            }
            else
            {
                var secondPage = new CheckOutPage(optionOneMealOrders.ToString(), optionTwoMealOrders.ToString());
                await Navigation.PushAsync(secondPage);
            }
        }

        private void reduceOrdersForMealOptionOne(object sender, System.EventArgs e)
        {
            if (optionOneMealOrders > 0)
            {
                optionOneMealOrders = optionOneMealOrders - 1;
                op1qty.Text = optionOneMealOrders.ToString();
                op1Price.Text = "$" + (optionOneMealOrders * 20).ToString();
            }
            else
            {
                op1qty.Text = optionOneMealOrders.ToString();
            }
        }

        private void addOrdersForMealOptionOne(object sender, System.EventArgs e)
        {
            if (optionOneMealOrders < 10)
            {
                optionOneMealOrders = optionOneMealOrders + 1;
                op1qty.Text = optionOneMealOrders.ToString();
                op1Price.Text = "$" + (optionOneMealOrders * 20).ToString();
            }
            else
            {
                op1qty.Text = optionOneMealOrders.ToString();
            }
        }

        private void updateOrdersForMealOptionOne(object sender, ValueChangedEventArgs e)
        {
            optionOneMealOrders = (int)e.NewValue;
            op1qty.Text = optionOneMealOrders.ToString();
        }

        private void reduceOrdersForMealOptionTwo(object sender, System.EventArgs e)
        {
            if (optionTwoMealOrders > 0)
            {
                optionTwoMealOrders = optionTwoMealOrders - 1;
                op2qty.Text = optionTwoMealOrders.ToString();
                op2Price.Text = "$" + (optionTwoMealOrders * 24).ToString();
            }
            else
            {
                op2qty.Text = optionTwoMealOrders.ToString();
            }
        }

        private void addOrdersForMealOptionTwo(object sender, System.EventArgs e)
        {
            if (optionTwoMealOrders < 10)
            {
                optionTwoMealOrders = optionTwoMealOrders + 1;
                op2qty.Text = optionTwoMealOrders.ToString();
                op2Price.Text = "$" + (optionTwoMealOrders * 24).ToString();
            }
            else
            {
                op2qty.Text = optionTwoMealOrders.ToString();
            }
        }

        private void updateOrdersForMealOptionTwo(object sender, ValueChangedEventArgs e)
        {
            optionTwoMealOrders = (int)e.NewValue;
            op2qty.Text = optionTwoMealOrders.ToString();
        }

        //leaving this function here for the meal photo GET request
        async Task getimg()
        {
            string uri = createUrl();


            var client = new HttpClient();
            System.Diagnostics.Debug.Print("about to make get request");
            //string uri = "https://s3-us-west-2.amazonaws.com/ordermealapp/" + date;
            Console.WriteLine(uri);
            Stream stream = await client.GetStreamAsync(uri);

            Image img = new Image();
            img.Source = ImageSource.FromStream(() => stream);

            mealPhoto.Source = img.Source;
        }
        public string createUrl()
        {
            DateTime dateTime = DateTime.UtcNow.Date;
            var today = dateTime.ToString("yyyyMMdd");

            string url = "https://s3-us-west-2.amazonaws.com/ordermealapp/" + today;
            return url;
        }
    }
}
