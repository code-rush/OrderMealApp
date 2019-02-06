using System;
using System.Collections.Generic;

using Xamarin.Forms;

namespace OrderMeal
{
    public partial class CheckOutPage : ContentPage
    {

        public CheckOutPage(string optionOneMeals, string optionTwoMeals)
        {
            InitializeComponent();
            Option1Count.Text = optionOneMeals;
            Option2Count.Text = optionTwoMeals;
            var totalMealOptionOnePrice = Convert.ToInt32(optionOneMeals) * 20;
            var totalMealOptionTwoPrice = Convert.ToInt32(optionTwoMeals) * 24;
            var tax = (totalMealOptionOnePrice + totalMealOptionTwoPrice) * 0.09;
            var totalPrice = totalMealOptionOnePrice + totalMealOptionTwoPrice + tax;
            Tax.Text = "$" + tax.ToString();
            TotalPrice.Text = "$" + totalPrice.ToString();

        }

        void Handle_Clicked(object sender, System.EventArgs e)
        {
            //var client = HttpClient();
        }
    }
}
